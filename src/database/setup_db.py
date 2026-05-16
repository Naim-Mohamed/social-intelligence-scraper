import pymysql

from config.settings import Passwords


def create_platform_tables(cursor, platform):
    for stage in ("raw", "filtered"):
        table_name = f"{platform}_{stage}"
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                keyword VARCHAR(255),
                content TEXT,
                post_url VARCHAR(512) NOT NULL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_{table_name}_post_url (post_url),
                INDEX idx_{table_name}_post_url (post_url)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        print(f"Table '{table_name}' is ready with duplicate guard.")


def main():
    pass_manager = Passwords()
    db_config = pass_manager.get_db_config()

    connection = pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        charset="utf8mb4",
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_config['database']} "
                "DEFAULT CHARACTER SET utf8mb4"
            )
            cursor.execute(f"USE {db_config['database']}")
            print(f"Database '{db_config['database']}' is ready.")

            for platform in ("twitter", "instagram", "linkedin"):
                create_platform_tables(cursor, platform)

        connection.commit()
        print("All duplicate-guard tables are ready.")
    finally:
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Database setup error: {type(error).__name__}: {error}")
