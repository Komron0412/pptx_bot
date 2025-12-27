---
description: how to build and run the bot using Docker
---

To build and run the bot using Docker, follow these steps:

1. **Ensure `.env` file exists**: Make sure you have a `.env` file in the root directory with all necessary API keys and configuration.

2. **Build and start the containers**:
   Run the following command to build the bot image and start both the bot and the PostgreSQL database in the background:
   ```bash
   docker compose up -d --build
   ```

3. **Check the logs**:
   To see the bot's logs and ensure everything is running correctly, use:
   ```bash
   docker compose logs -f bot
   ```

4. **Stop the bot**:
   To stop the bot and the database, run:
   ```bash
   docker compose down
   ```

> [!NOTE]
> The Docker setup uses a persistent volume for the PostgreSQL database, so your user data will be saved even if you stop or rebuild the containers.

> [!TIP]
> If you make changes to the code, you only need to run `docker compose up -d --build` again to apply them.
