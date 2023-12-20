use pyo3::{prelude::*, types::{PyDict, PyList}};
use cedar_policy as cedar;


#[pyclass]
struct EntityUid(cedar::EntityUid);

#[pymethods]
impl EntityUid {
    #[new]
    fn new(type_name: &str, name: &str) -> Self {
        let type_name = type_name.parse().expect("invalid type_name");
        let name = name.parse().expect("invalid id");
        Self(cedar::EntityUid::from_type_name_and_id(type_name, name))
    }
}

#[pyclass]
struct Request(cedar::Request);

#[pymethods]
impl Request {
    #[new]
    fn new(principal: Option<&str>, action: Option<&str>, resource: Option<&str>, context: Option<&PyDict>, py: Python) -> Self {
        let context = context.map(|c| {
            let json = py.import("json").expect("failed to import json");
            let json_str = json
                .call_method1("dumps", (c,))
                .expect("failed to dump json")
                .extract::<String>()
                .expect("failed to extract json");
            cedar::Context::from_json_str(&json_str, None).expect("invalid context")
        }).unwrap_or_else(|| cedar::Context::empty());

        Self(
            cedar::Request::new(
                principal.map(|p| p.parse().unwrap()),
                action.map(|a| a.parse().unwrap()),
                resource.map(|r| r.parse().unwrap()),
                context,
                None
            ).unwrap()
        )
    }
}

#[pyclass]
struct PolicySet(cedar::PolicySet);

#[pymethods]
impl PolicySet {
    #[new]
    fn new(policies_str: &str) -> Self {
        Self(policies_str.parse().expect("invalid policies"))
    }
}

#[pyclass]
struct Entities(cedar::Entities);

#[pymethods]
impl Entities {
    #[new]
    fn new(value: &PyList, py: Python) -> Self {
        let json = py.import("json").expect("failed to import json");
        let json_str = json
            .call_method1("dumps", (value,))
            .expect("failed to dump json")
            .extract::<String>()
            .expect("failed to extract json");
        Self(cedar::Entities::from_json_str(&json_str, None).expect("invalid entities"))
    }
}

#[pyclass]
struct Authorizer(cedar::Authorizer);

#[pymethods]
impl Authorizer {
    #[new]
    fn new() -> Self {
        Self(cedar::Authorizer::new())
    }

    fn is_authorized(&self, request: &Request, policy_set: &PolicySet, entities: Option<&Entities>) -> Response {
        let response = match entities {
            Some(entities) => self.0.is_authorized(&request.0, &policy_set.0, &entities.0),
            None => self.0.is_authorized(&request.0, &policy_set.0, &cedar::Entities::empty()),
        };
        Response::create(response)
    }
}

#[pyclass]
struct Response{
    response: cedar::Response,
    decision: Decision,
    is_allowed: bool,
}

impl Response {
    fn create(response: cedar::Response) -> Self {
        let desision = match response.decision() {
            cedar::Decision::Allow => Decision::Allow,
            cedar::Decision::Deny => Decision::Deny,
        };
        let allowed = response.decision() == cedar::Decision::Allow;

        Self {
            response: response,
            decision: desision,
            is_allowed: allowed,
        }
    }
}

#[pymethods]
impl Response {
    fn diagnostics(&self) -> String {
        self.response.diagnostics().errors().map(|r| r.to_string()).collect()
    }

    #[getter]
    fn decision(&self) -> Decision {
        self.decision.clone()
    }

    #[getter]
    fn is_allowed(&self) -> bool {
        self.is_allowed
    }
}

#[pyclass]
#[derive(Clone)]
enum Decision {
    Allow,
    Deny,
}

/// A Python module implemented in Rust.
#[pymodule]
fn yacedar(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<EntityUid>()?;
    m.add_class::<Request>()?;
    m.add_class::<PolicySet>()?;
    m.add_class::<Entities>()?;
    m.add_class::<Authorizer>()?;
    m.add_class::<Response>()?;
    m.add_class::<Decision>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_entity_uid() {
        let entity_uid = EntityUid::new("type", "name");
        assert_eq!(entity_uid.0.type_name().to_string(), "type");
        assert_eq!(entity_uid.0.id().to_string(), "name");
    }
}
