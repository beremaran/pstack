# Companion TypeScript conventions

Apply when reviewing TypeScript. These were always-applied rules in the upstream companion plugin; this port scopes them to relevant reviews.



# No inline imports

Always place imports at the top of the module. Avoid inline imports in function bodies, type annotations, or interface fields unless there is a strict circular-dependency reason and it is documented.



typescript-exhaustive-switch: In switch statements over discriminated unions or enums, use a `never` check in the default case so newly added variants cause compile-time failures until handled.
