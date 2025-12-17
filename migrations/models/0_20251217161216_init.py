from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "project_runtime" (
    "id" UUID NOT NULL PRIMARY KEY,
    "project_name" VARCHAR(255) NOT NULL UNIQUE,
    "project_root" TEXT NOT NULL,
    "container_name" VARCHAR(255) NOT NULL UNIQUE,
    "image" VARCHAR(255) NOT NULL DEFAULT 'python:3.11-slim',
    "status" VARCHAR(32) NOT NULL DEFAULT 'stopped',
    "last_command" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_project_run_project_fea029" ON "project_runtime" ("project_name");
COMMENT ON TABLE "project_runtime" IS 'Persistent runtime state for each generated project.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztl21P2zAQgP9KlE9Mgoqm5UVomtRBNzpBiyBsCIQiN3bbjMQOtjOoEP99Ptdp2qQpFF"
    "iBiS9Vcy/2+Tnb57uzI4ZJKCpHnP0mvjxOqAwiYu9YdzZF+k+JxaplozjO9CCQqBtql3hk"
    "6/EJ466QHPlSqXsoFESJMBE+D2IZMApOR4SLQEhCpWX8LCGRJFaPcYsgf2D1CSVcSbBlJq"
    "jAyJj5auiA9p8zSEKD64R4kvWJHBCuhrq4VOKAYnJLRPoZX3m9gIR4ik+AYQAt9+Qw1rLT"
    "09beN20JAXY9n4VJRDPreCgHjI7NkyTAFfAB3TjACVQ0CUMDNxWNIlYCyRMyDhVnAkx6KA"
    "kBuP25l1AfOFt6Jvipf7ELKYBZckCNyGcU0hdQCSzu7kerytaspTZMtbvfOF6pbX7Sq2RC"
    "9rlWaiL2vXZEEo1cNdcMZLpr9HcB6e4A8dlI8345uCrwf4M1xfU0hnaEbr2Q0L4cqE9nY2"
    "MO1J+NY81VWWmwTJ2k0UlrG5Uz0gHgIlDOmCwCdcmtnA809XsZoKkgI5pdBC+DdA5Bt3nm"
    "QtCRENfhJLiVw8aZZhoNjeag0/6emk+A3j3ofM3xVdNLNTnhC2/ZoufHpk2v0wj1F2I5dl"
    "jeNjVT7dQq1eqaCIPoGXfpEpBCBUzEIkwzjyVCFZLFMcEvxrLmPAJlzSklCappkCESUlGK"
    "IkRnFP3yCzXv9ySo5ij/z/cpJ7B8D82oVntKA8+5kvt0yjOHFxvXSvrnbVYvW60Bd2g4NL"
    "meR7912DxxG4dHUynYa7hN0DhT+FPpymZuo48HsX613H0LPq3zTruZf7mN7dxzG2JCiWQe"
    "ZTcewhMVJpWmYKYSm8T4iYmd9vxI7KsmVgcPfVDvauIBD4Iu8q9uEMdeQcMcVmZbVEVOlJ"
    "cgqqo7NmwhStOONggP/IE9o1E1mtV5DSrKbB7qS8vT/MI9Y4uWVI+ZLaPaXPndbhL2qu/D"
    "Psyy5lTrW/Xt2mZ9W5noSMaSrTm7v9V2H2gR/0B7r0Ja4Ckz4fJe+pglPAnhaCwA0Zi/T4"
    "DV9fVHAFRWpQC1rtj7ETqjnv046bTLmz7jkgN5StUCL3Dgy1UrDIS8fJtY51CEVc9/D+af"
    "frliBAPAe/BVy8v9X6FQwno="
)
