DROP TABLE IF EXISTS alert_subscription;
DROP TABLE IF EXISTS restriction;
DROP TABLE IF EXISTS decree;
DROP TABLE IF EXISTS geozone;

------

CREATE TABLE public.geozone (
    gid SERIAL PRIMARY KEY,
    id character varying(32),
    dpt character varying(3),
    type character varying(3),
    libel character varying(200),
    geom public.geometry(MultiPolygon, 4326)
);

CREATE TABLE decree(
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(25) NOT NULL UNIQUE,
    geozone_id INT REFERENCES geozone (gid) NOT NULL,
    alert_level VARCHAR(100) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL
);

CREATE TABLE restriction (
    id SERIAL PRIMARY KEY,
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
    geozone_id INT REFERENCES geozone (gid) NOT NULL,
    subscribed_at date NOT NULL
);
