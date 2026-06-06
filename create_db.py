import argparse
import json
import sqlite3
from pathlib import Path



def create_tables(conn: sqlite3.Connection):
    sql_path = Path(__file__).with_name('tables.sql')
    if not sql_path.exists():
        raise FileNotFoundError(f'SQL schema file not found: {sql_path}')

    conn.executescript(sql_path.read_text(encoding='utf-8'))



def disable_checks(conn: sqlite3.Connection):
    conn.execute('PRAGMA foreign_keys = OFF;')
    conn.execute('PRAGMA ignore_check_constraints = ON;')



def enable_checks(conn: sqlite3.Connection):
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.execute('PRAGMA ignore_check_constraints = OFF;')



def check_data(conn: sqlite3.Connection):
    cursor = conn.execute('PRAGMA foreign_key_check;')
    errors = cursor.fetchall()
    if errors:
        raise Exception('Data integrity check failed due to foreign key violations.')
    print('No foreign key violations found.')

    cursor = conn.execute('PRAGMA integrity_check;')
    errors = cursor.fetchall()
    if errors:
        if len(errors) != 1 and errors[0][0] != 'ok':
            raise Exception('Data integrity check failed due to data integrity violations.')
    print('No data integrity violations found.')



def ensure_object_types(conn: sqlite3.Connection):
    conn.executemany(
        'INSERT OR IGNORE INTO "OBJECT_TYPES" (OBJECT_TYPE_ID, NAME) VALUES (?, ?)',
        [
            (1, 'GOI'),
            (2, 'HUBS'),
            (3, 'ITEMS'),
            (4, 'TALES'),
        ],
    )



def insert_goi(conn: sqlite3.Connection, goi_path: Path):
    goi_data = load_json(goi_path)

    for item in goi_data:
        item_data = goi_data.get(item)

        conn.execute(
            '''INSERT OR REPLACE INTO "UNIVERSAL_FIELDS" (
                LINK, PAGE_ID, CREATED_AT, CREATOR, URL, OBJECT_TYPE_ID, DOMAIN
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                item_data.get('link'),
                item_data.get('page_id'),
                item_data.get('created_at'),
                item_data.get('creator'),
                item_data.get('url'),
                1,
                item_data.get('domain'),
            ),
        )

        conn.execute(
            '''INSERT OR REPLACE INTO "GOI" (
                LINK, TITLE, RATING, RAW_CONTENT, RAW_SOURCE
            ) VALUES (?, ?, ?, ?, ?)''',
            (
                item_data.get('link'),
                item_data.get('title'),
                item_data.get('rating'),
                item_data.get('raw_content'),
                item_data.get('raw_source'),
            ),
        )

        for history_item in item_data.get('history'):
            conn.execute(
                '''INSERT OR REPLACE INTO "HISTORY" (
                    LINK, AUTHOR, AUTHOR_HREF, COMMENT, DATE
                ) VALUES (?, ?, ?, ?, ?)''',
                (
                    item_data.get('link'),
                    history_item.get('author'),
                    history_item.get('author_href'),
                    history_item.get('comment'),
                    history_item.get('date'),
                ),
            )

        for image in item_data.get('images'):
            conn.execute(
                'INSERT OR REPLACE INTO "IMAGES" (LINK, IMAGE_URL) VALUES (?, ?)',
                (
                    item_data.get('link'),
                    image,
                ),
            )

        ### TODO
        # for hub in item_data.get('hubs'):
        #     conn.execute(
        #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
        #         (
        #             hub,
        #             item_data.get('link')
        #         ),
        #     )



def insert_hubs(conn: sqlite3.Connection, hubs_path: Path):
    hubs_data = load_json(hubs_path)

    for item in hubs_data:
        item_data = hubs_data.get(item)

        conn.execute(
            '''INSERT OR REPLACE INTO "UNIVERSAL_FIELDS" (
                LINK, PAGE_ID, CREATED_AT, CREATOR, URL, OBJECT_TYPE_ID, DOMAIN
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                item_data.get('link'),
                item_data.get('page_id'),
                item_data.get('created_at'),
                item_data.get('creator'),
                item_data.get('url'),
                2,
                item_data.get('domain'),
            ),
        )

        conn.execute(
            '''INSERT OR REPLACE INTO "HUBS" (
                LINK, TITLE, RAW_CONTENT
            ) VALUES (?, ?, ?)''',
            (
                item_data.get('link'),
                item_data.get('title'),
                item_data.get('raw_content'),
            ),
        )

        for history_item in item_data.get('history'):
            conn.execute(
                '''INSERT OR REPLACE INTO "HISTORY" (
                    LINK, AUTHOR, AUTHOR_HREF, COMMENT, DATE
                ) VALUES (?, ?, ?, ?, ?)''',
                (
                    item_data.get('link'),
                    history_item.get('author'),
                    history_item.get('author_href'),
                    history_item.get('comment'),
                    history_item.get('date'),
                ),
            )

        ### TODO
        # for ref in item_data.get('references'):
        #     conn.execute(
        #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
        #         (
        #             item_data.get('link'),
        #             ref
        #         ),
        #     )



def insert_items(conn: sqlite3.Connection, item_paths: list[Path]):
    for item_path in item_paths:

        items_data = load_json(item_path)

        for item in items_data:

            item_data = items_data.get(item)

            conn.execute(
                '''INSERT OR REPLACE INTO "UNIVERSAL_FIELDS" (
                    LINK, PAGE_ID, CREATED_AT, CREATOR, URL, OBJECT_TYPE_ID, DOMAIN
                ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    item_data.get('link'),
                    item_data.get('page_id'),
                    item_data.get('created_at'),
                    item_data.get('creator'),
                    item_data.get('url'),
                    3,
                    item_data.get('domain'),
                ),
            )

            conn.execute(
                '''INSERT OR REPLACE INTO "ITEMS" (
                    LINK, TITLE, RATING, SCP, SCP_NUMBER, SERIES, RAW_CONTENT, RAW_SOURCE
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    item_data.get('link'),
                    item_data.get('title'),
                    item_data.get('rating'),
                    item_data.get('scp'),
                    item_data.get('scp_number'),
                    item_data.get('series'),
                    item_data.get('raw_content'),
                    item_data.get('raw_source'),
                ),
            )

            for history_item in item_data.get('history'):
                conn.execute(
                    '''INSERT OR REPLACE INTO "HISTORY" (
                        LINK, AUTHOR, AUTHOR_HREF, COMMENT, DATE
                    ) VALUES (?, ?, ?, ?, ?)''',
                    (
                        item_data.get('link'),
                        history_item.get('author'),
                        history_item.get('author_href'),
                        history_item.get('comment'),
                        history_item.get('date'),
                    ),
                )

            for image in item_data.get('images'):
                conn.execute(
                    'INSERT OR REPLACE INTO "IMAGES" (LINK, IMAGE_URL) VALUES (?, ?)',
                    (
                        item_data.get('link'),
                        image,
                    ),
                )

            ### TODO
            # for hub in item_data.get('hubs'):
            #     conn.execute(
            #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
            #         (
            #             hub,
            #             item_data.get('link')
            #         ),
            #     )
            
            # for ref in item_data.get('references'):
            #     conn.execute(
            #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
            #         (
            #             item_data.get('link'),
            #             ref
            #         ),
            #     )



def insert_tales(conn: sqlite3.Connection, tale_paths: list[Path]):
    for tale_path in tale_paths:
        tales_data = load_json(tale_path)

        for tale in tales_data:

            tale_data = tales_data.get(tale)

            conn.execute(
                '''INSERT OR REPLACE INTO "UNIVERSAL_FIELDS" (
                    LINK, PAGE_ID, CREATED_AT, CREATOR, URL, OBJECT_TYPE_ID, DOMAIN
                ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    tale_data.get('link'),
                    tale_data.get('page_id'),
                    tale_data.get('created_at'),
                    tale_data.get('creator'),
                    tale_data.get('url'),
                    4,
                    tale_data.get('domain'),
                ),
            )

            conn.execute(
                '''INSERT OR REPLACE INTO "TALES" (
                    LINK, TITLE, RATING, YEAR, RAW_CONTENT, RAW_SOURCE
                ) VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    tale_data.get('link'),
                    tale_data.get('title'),
                    tale_data.get('rating'),
                    tale_data.get('year'),
                    tale_data.get('raw_content'),
                    tale_data.get('raw_source'),
                ),
            )

            for history_item in tale_data.get('history'):
                conn.execute(
                    '''INSERT OR REPLACE INTO "HISTORY" (
                        LINK, AUTHOR, AUTHOR_HREF, COMMENT, DATE
                    ) VALUES (?, ?, ?, ?, ?)''',
                    (
                        tale_data.get('link'),
                        history_item.get('author'),
                        history_item.get('author_href'),
                        history_item.get('comment'),
                        history_item.get('date'),
                    ),
                )

            for image in tale_data.get('images'):
                conn.execute(
                    'INSERT OR REPLACE INTO "IMAGES" (LINK, IMAGE_URL) VALUES (?, ?)',
                    (
                        tale_data.get('link'),
                        image,
                    ),
                )

            ### TODO
            # for hub in tale_data.get('hubs'):
            #     conn.execute(
            #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
            #         (
            #             hub,
            #             tale_data.get('link')
            #         ),
            #     )
            
            # for ref in tale_data.get('references'):
            #     conn.execute(
            #         'INSERT OR REPLACE INTO "REFERENCES" (PARENT_LINK, CHILD_LINK) VALUES (?, ?)',
            #         (
            #             tale_data.get('link'),
            #             ref
            #         ),
            #     )



def get_sub_paths(index: dict, sub_folder: str) -> list[Path]:
    item_paths = []
    for item, path in index.items():
        path = source_root / sub_folder / (path.split('/')[len(path.split('/')) - 1])
        item_paths.append(path)
    return item_paths



def load_json(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert SCP JSON files to an SQLite database.')
    parser.add_argument('--source', default='../scp-api/docs/data/scp/', help='Source root for SCP JSON data. Required')
    parser.add_argument('--output', default='scp.db', help='Output SQLite database file. Default: ./scp_data.db')
    args = parser.parse_args()

    source_root = Path(args.source)
    if not source_root.exists():
        raise FileNotFoundError(f'Source directory not found: {source_root}')

    goi_path = source_root / 'goi' / 'content_goi.json'
    hubs_path = source_root / 'hubs' / 'index.json'
    items_index = source_root / 'items' / 'content_index.json'
    items_paths = get_sub_paths(load_json(items_index), 'items')
    tales_index = source_root / 'tales' / 'content_index.json'
    tales_paths = get_sub_paths(load_json(tales_index), 'tales')
 
    output_path = Path(args.output)
    if output_path.exists():
        print(f'Removing existing SQLite file: {output_path}')
        output_path.unlink()

    print(f'Creating SQLite database: {output_path}')
    conn = sqlite3.connect(str(output_path))
    try:
        create_tables(conn)
        print('Tables created...')
        disable_checks(conn)
        ensure_object_types(conn)
        print('Object types initialized...')
        insert_goi(conn, goi_path)
        print('GOI created...')
        insert_hubs(conn, hubs_path)
        print('Hubs created...')
        insert_items(conn, items_paths)
        print('Items created...')
        insert_tales(conn, tales_paths)
        print('Tales created...')
        enable_checks(conn)
        check_data(conn)
        conn.commit()
    finally:
        conn.close()

    print('Conversion complete!')
