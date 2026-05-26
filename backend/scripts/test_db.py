import asyncio
import asyncpg

async def main():
    try:
        c = await asyncpg.connect(
            host="127.0.0.1", port=5433,
            user="ulockai", password="ulockai_secret", database="ulockai_shield"
        )
        print("127.0.0.1 OK")
        await c.close()
    except Exception as e:
        print(f"127.0.0.1 FAIL: {e}")
    try:
        c = await asyncpg.connect(
            host="localhost", port=5432,
            user="ulockai", password="ulockai_secret", database="ulockai_shield"
        )
        print("localhost OK")
        await c.close()
    except Exception as e:
        print(f"localhost FAIL: {e}")

asyncio.run(main())
