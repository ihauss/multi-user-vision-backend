# multi-user-vision-backend
Backend build for multiple user to separate usages


## Limitations (Intentional)

This project is a functional prototype and not production-ready.

Known limitations:
- Minimal security (hardcoded secret, no rate limiting, basic auth handling)
- API key lookup not optimized for scalability
- No strict input validation (payload size, formats, user inputs)
- Inconsistent behavior between in-memory and Redis repositories
- No pagination for events (potential performance issues at scale)
- No fault tolerance (e.g., Redis failures not handled)

These aspects are documented in the code and planned for future improvements.


## Future

Phase 1
* upgrade backend security
* camera SDK
* minimal UI
Phase 2
* pagination + filters
* websocket events
Phase 3
* images storage
* AI pipeline
