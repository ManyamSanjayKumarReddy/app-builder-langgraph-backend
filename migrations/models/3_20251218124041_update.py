from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" DROP COLUMN "process_command";
        ALTER TABLE "project_runtime" DROP COLUMN "process_status";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_runtime" ADD "process_command" TEXT;
        ALTER TABLE "project_runtime" ADD "process_status" VARCHAR(20) NOT NULL DEFAULT 'stopped';"""


MODELS_STATE = (
    "eJztmOtPGzkQwP8Vaz9RieRKoLRCp0opj2tOkEQQri+qyKwniS9ee2t7KRHif78ZZzePza"
    "OF46A9lQ8oOw+P/ZtZe7w3UWIEKFdtW/M3xP40014mEO2xm0jz8GOFxSaLeJpO9STw/FIF"
    "l3Rs27UzxpfOWx57VPe4coAiAS62MvXSaHJqg3XSedCe5X7Mee6B9YxlwOMB64MGixLB8g"
    "BVGlmYGIeWun/fQS70hT4AJ/uatXGcWKYK3N6Friz8oYy94fEQtGAJ17wPjrWaxx+YHwA7"
    "MKiwLDbac4kxmJI9iEexgir51dNUyZjTailyDM6h98aR4m7IfmNH3Pl6u4G/zrwFnijp8T"
    "dG0N49u9CMcQssc2ArFMAapXAFV5Kzd3B5RpE982ATqbkK4ZqGXY5nWlFwBaqIySgLQ6TF"
    "pGMpWOSSgAgMOgMUhWwyqQkhTpUrNWL8ykjhihHy8QLWC+0NylGAwENeGXJOpFPABQUpki"
    "A1BQqrD0nLtPySQdebPiA7i6n79BnFUgu4Blc8psNuT4ISc/UoBQ0Q5F0/SoPs/LxxcBQs"
    "qSAuu7FRWaKn1unID4yemGeZFFXyId2kIGZKU2dK5cVciMYzRoG3GUymKqYCAT2eKSrw6P"
    "depuOQ6RCJ/u28jhZKnqKUCjgXYY7pdcE0EIub2/GqpmsO0ohC7b+tn25s7z4LqzTO921Q"
    "BiLRbXDkno9dA9cpyOItDc8LSPcH3C5HWvYrwcWJ/zdYC1z3Yxgl/LqrQPf9AB9rL16sgf"
    "pX/TRwRasA1uA7M97ZmrmqNtYR4EWg1hi/CLQD13490MLvYYAWginR6cb7MEjXEOwcvu/Q"
    "pBPnvqhZcBsn9feBaTLKNcet5h+F+Qzo/ePWmxLfydZ655Jd9PxVtMV2muAhcxeWE4fHK9"
    "M81N52dWur4pRM/sVe+ghI6WjM3F2YTj0eEarzJk1BPBjL7dp3oNyurSRJqnmQ2Bt5pJRg"
    "r7Xk0F+9oZb97gU1f5X/z/spNpq4/C5fclodoIY6txX76ZxnCa/IXavFjx/z9IpwDaKl1S"
    "jP9Tr6jZPDs079pD2XgoN655A0tTn8hXRjt1Tok0HYu0bnLaNH9rHVPCx3bhO7zseI5sQz"
    "b7rafO1yMXPCFNICzFxis1TcM7Hznr8S+6SJDZOne1BvONPAk4Cudl+5Fd0FjamZVbaLqq"
    "SWlCXhVitytjTL/PpfByvjQbTkw0Cu2Vz3QYBPbb71HWB1mh/4ztjQK06PpVdGLK5ytecJ"
    "e9L+sE9RKrWtnZc7r7Z3d16hSZjJRPJyTfU3mp1vXBGv6HMKTukOrcyMy89yj3mElpBejT"
    "tAzM1/ToBbz59/B0C0Wgkw6BbvfqCXnGd/nrWaqy99uUsJ5LnGBX4SMvabTEnnP/+YWNdQ"
    "pFWv7wfLrV/pMKIBqB980uPl9h993kX/"
)
