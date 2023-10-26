use std::str::FromStr;

use pyo3::{prelude::*, types::{PyDict, PyList}};
use cedar_policy as cedar;


#[pyclass]
struct EntityUid(cedar::EntityUid);

#[pymethods]
impl EntityUid {
    #[new]
    fn new(type_name: &str, name: &str) -> Self {
        let type_name = cedar::EntityTypeName::from_str(type_name).expect("invalid type_name");
        let name = cedar::EntityId::from_str(name).expect("invalid id");
        Self(cedar::EntityUid::from_type_name_and_id(type_name, name))
    }
}

#[pyclass]
struct Context(cedar::Context);

#[pymethods]
impl Context {
    #[new]
    fn new(value: &PyDict, py: Python) -> Self {
        let json = py.import("json").expect("failed to import json");
        let json_str = json
            .call_method1("dumps", (value,))
            .expect("failed to dump json")
            .extract::<String>()
            .expect("failed to extract json");
        Self(cedar::Context::from_json_str(&json_str, None).expect("invalid context"))
    }
}

#[pyclass]
struct Request(cedar::Request);

#[pymethods]
impl Request {
    #[new]
    fn new(principal: Option<&EntityUid>, action: Option<&EntityUid>, resource: Option<&EntityUid>, context: Option<&Context>) -> Self {
        let principal = principal.map(|p| p.0.clone());
        let action = action.map(|a| a.0.clone());
        let resource = resource.map(|r| r.0.clone());
        let context = context.map(|c| c.0.clone()).unwrap_or(cedar::Context::empty());

        Self(cedar::Request::new(principal, action, resource, context))
    }
}

#[pyclass]
struct PolicySet(cedar::PolicySet);

#[pymethods]
impl PolicySet {
    #[new]
    fn new(policies_str: &str) -> Self {
        Self(cedar::PolicySet::from_str(policies_str).expect("invalid policies"))
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
        self.response.diagnostics().reason().map(|r| r.to_string()).collect()
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
    m.add_class::<Context>()?;
    m.add_class::<Request>()?;
    m.add_class::<PolicySet>()?;
    m.add_class::<Entities>()?;
    m.add_class::<Authorizer>()?;
    m.add_class::<Response>()?;
    m.add_class::<Decision>()?;
    Ok(())
}
