from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" ADD "process_status" VARCHAR(20) NOT NULL DEFAULT 'stopped';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" DROP COLUMN "process_status";"""


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlE9MgqpNy4vQNKmDbnSCFkHYEAhFbuy2GYkdYmdQIf77fK7TtEkTKH"
    "QFJr5Uzb3Y58cX+y73ZsAw8XnlOGK/iStOYiq8gJi7xr1JkfpTYLFumCgMUz0IBOr5yiUc"
    "2zrRlHGPiwi5Qqr7yOdEijDhbuSFwmMUnI5JxD0uCBWG9jO4QIIYfRYZBLlDY0AoiaQEG3"
    "qCCoyMmSuH9ujgJYPE1LuJiSPYgIghieRQl1dS7FFM7ghPHsNrp+8RH8/w8TAMoOSOGIVK"
    "dnbW3v+mLCHAnuMyPw5oah2OxJDRiXkce7gCPqCbBDiFisa+r+EmonHEUiCimExCxakAkz"
    "6KfQBufu7H1AXOhpoJfhpfzNwWwCwZoFrkMgrb51EBLO4fxqtK16ykJky1d9A8WatvfVKr"
    "ZFwMIqVURMwH5YgEGrsqrinIJGvUcw7p3hBF85Fm/TJwZeD/BmuC63kMzQDdOT6hAzGUj9"
    "bmZgnUn80TxVVaKbBMvknjN62jVdZYB4DzQCPGRB6oTe5EOdDEbzlAE0FKND0IloO0hKDd"
    "Orch6IDzG38a3NpR81wxDUZac9jtfE/Mp0DvHXa/ZvjK6YWcnEQLp2ze8yNpk+M0QIOFWE"
    "4cVpemeqrdeqVW2+C+F7zgLF0BUrgBY74I09RjhVC5YGFI8NJY1q0noKxbhSRBNQvSR1xI"
    "SkGA6JxLv/hAzfo9C6p+lf/j81TeOy7h3Fk8X/Oe7zhvrepTjoBq8QlQzeatGxFYtIPmlA"
    "H7UgN1csFFNeOZgYq1ayX58zbLAlOuAXepP9IvUVlat49ap3bz6Hgmt/ebdgs01kxeJ9K1"
    "rcxOTAYxfrXtAwMejYtup5UtiSd29oUJMaFYMIeyWwfhqas7kSZgZjY2DvEzN3bW82NjX3"
    "VjVfDQYPavpzojEPSQe32LIuzkNMxiRbZ5VWAFWQmismzCmi1Eqfv8Jok8d2jO+QKgNetl"
    "nT9KbR5r+Iu3ecnNeJsWXMtze3GZXNls1xv2qoX3AGbZsGqN7cZOfauxI01UJBPJdkn2tz"
    "v2I733H/huIkNa4M6dcnkvDeIKam14NRaAqM3fJ8Ba9SmVirQqBKh0+aaa0Dn32Y/Tbqe4"
    "m9YuGZBnVC7wEnuuWDd8j4urt4m1hCKsurzQztbUmcsIBoBC+1Wvl4e/riUyJQ=="
)
