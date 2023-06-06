DROP TABLE IF EXISTS alert_subscription;
DROP TABLE IF EXISTS restriction;
DROP TABLE IF EXISTS decree;
DROP TABLE IF EXISTS geozone;

------

CREATE TABLE geozone (
    id SERIAL PRIMARY KEY,
    id_zone INT,
    code_zone VARCHAR(32),
    type_zone VARCHAR(3),
    nom_zone VARCHAR(200),
    n_version INT,
    code_dep VARCHAR(3),
    nom_dep VARCHAR(60),
    geom geometry(MultiPolygon, 4326)
);

CREATE TABLE decree(
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(32) NOT NULL UNIQUE,
    geozone_id INT REFERENCES geozone (id) NOT NULL,
    alert_level VARCHAR(100) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    document TEXT NOT NULL
);

CREATE TABLE restriction (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(64) NOT NULL UNIQUE,
    decree_id INT REFERENCES decree (id) NOT NULL,
    restriction_level VARCHAR(100) NOT NULL,
    user_individual BOOLEAN NOT NULL,
    user_company BOOLEAN NOT NULL,
    user_community BOOLEAN NOT NULL,
    user_farming BOOLEAN NOT NULL,
    theme VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    specification TEXT,
    from_hour SMALLINT,
    to_hour SMALLINT
);

CREATE TABLE alert_subscription (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    subscribed_at date NOT NULL
);
