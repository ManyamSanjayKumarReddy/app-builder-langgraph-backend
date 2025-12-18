from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" ADD "process_command" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" DROP COLUMN "process_command";"""


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlE9MgqpNy4vQNKmDbnSCFkHYEAhFbuy2GYkdYmdQIf77fK7TtEkTaG"
    "EFJr5Uzb3Y58f22b57M2CY+LxyHLHfxBUnMRVeQMxd496kSP0psFg3TBSGqR4EAvV85RKO"
    "bZ1oyrjHRYRcIdV95HMiRZhwN/JC4TEKTsck4h4XhApD+xlcIEGMPosMgtyhMSCURFKCDd"
    "1BBVrGzJVNe3TwnEZi6t3ExBFsQMSQRLKpyysp9igmd4Qnn+G10/eIj2f4eBgaUHJHjEIl"
    "Oztr739TlhBgz3GZHwc0tQ5HYsjoxDyOPVwBH9BNApxCRWPf13AT0ThiKRBRTCah4lSASR"
    "/FPgA3P/dj6gJnQ/UEP40vZm4KoJcMUC1yGYXp86gAFvcP41GlY1ZSE7raO2ierNW3PqlR"
    "Mi4GkVIqIuaDckQCjV0V1xRksmrUdw7p3hBF85Fm/TJwZeD/BmuCazmGZoDuHJ/QgRjKT2"
    "tzswTqz+aJ4iqtFFgmd9J4p3W0yhrrAHAeaMSYyAO1yZ0oB5r4vQzQRJASTRPByyAtIWi3"
    "zm0IOuD8xp8Gt3bUPFdMg5HWHHY73xPzKdB7h92vGb6yeyE7J9HCSzbv+bFok3QaoMFCLC"
    "cOq1umuqvdeqVW2+C+Fzwjl64AKZyAMV+EaeqxQqhcsDAk+MVY1q0noKxbhSRBNQvSR1xI"
    "SkGA6JxDvzihZv2Wgqq38n+cT+W54xLOlyE8x/UDcinkxZNC3vMdJwer+pQ8Wy1Os9Vscn"
    "AjAoN20Jy71r7UwGOk4DYw45mBirVrJfnzNu9ephwD7lJ/pDdR2bJuH7VO7ebR8cza3m/a"
    "LdBYM+s6ka5tZWZi0ojxq20fGPBpXHQ7rey7Y2JnX5gQE4oFcyi7dRCeuh8l0gTMzMTGIV"
    "5yYmc9Pyb2VSdWBQ+v+P711PMTBD3kXt+iCDs5DbNYkW1eFVhBVoKovJtizRai1MWUJok8"
    "d2jOKbNozXpZeQWlNo9VVYqn+YUrHm1acDLPLXjIxZVd7XrCXvV1M4BeNqxaY7uxU99q7E"
    "gTFclEsl2y+tsd+5ECxx8oTsmQFjhzp1zeyyt8BQ8a2BoLQNTm7xNgrfqUm4q0KgSodPnK"
    "BaFzzrMfp91OcclCu2RAnlE5wEvsuWLd8D0urt4m1hKKMOryi3b2Tp05jKABuGi/6vHy8B"
    "d6faTm"
)
