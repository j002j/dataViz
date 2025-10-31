A project inspired by the meme starterkits but with connected to data science. 
![example starterkit Düsseldorf by 1Live ](./assets/kit_ddorf_wdr.png) [Link](https://www.instagram.com/p/CjIG-0EKhWb/?utm_source=ig_web_copy_link)


# PostgreSQL Database Setup for Starterkit
*Prerequisites*
- VS Code installiert
- Docker installiert und lauffähig
- Python 3.x installiert
- VS Code Extensions:
-   SQLTools: https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-pg 
-   SQLTools PostgreSQL/Cockroach Driver: https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools 

*Start PostgreSQL with Docker*
1. Check if Docker is installed: docker --version
2. Start PostgreSQL using Docker Compose: docker compose up -d
3. Check if the container is running: docker ps
4. you should see something like: 
        CONTAINER ID   IMAGE         COMMAND                  STATUS         PORTS
        123abc456def   postgres:15   "docker-entrypoint.s…"   Up 2 minutes   0.0.0.0:5432->5432/tcp

*Connect Postgres in VS code (manually)*
1. Open VS Code → SQLTools → Add New Connection
2. add settings:
    - Host: localhost
    - Port: 5432
    - DB: starterkit_db
    - User: jenny
    - PW: postgres
3. Test connection

*Connect Postgres in VS code (via script)*
1. run python init_db.py
2. output should be:
        Connected to starterkit_db at localhost:5432
        Executed SQL from db/starterkit.session.sql
        Connection closed.

*Notes on the database*
- Starterkit.session.sql contains the table schema
- if the table schema changes (by editing/updating the .sql) rerun: python init_db.py