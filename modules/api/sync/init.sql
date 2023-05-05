DROP TABLE IF EXISTS alert_subscription;
DROP TABLE IF EXISTS restriction;
DROP TABLE IF EXISTS decree;
DROP TYPE IF EXISTS alert_level;
DROP TYPE IF EXISTS restriction_level;

------

CREATE TYPE alert_level AS ENUM ('alerte', 'alerte_renforcee', 'vigilance', 'crise');
CREATE TYPE restriction_level AS ENUM ('interdiction', 'interdiction_exception', 'interdiction_plage_horaire', 'reduction', 'sensibilisation');

CREATE TABLE decree(
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(25) NOT NULL UNIQUE,
    geozone_id INT REFERENCES geozone (gid) NOT NULL,
    alert_level alert_level NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL
);

CREATE TABLE restriction (
    id SERIAL PRIMARY KEY,
    decree_id INT REFERENCES decree (id) NOT NULL,
    restriction_level restriction_level NOT NULL,
    user_individual BOOLEAN NOT NULL,
    user_company BOOLEAN NOT NULL,
    user_community BOOLEAN NOT NULL,
    user_farming BOOLEAN NOT NULL,
    theme VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    specification VARCHAR(255),
    from_hour SMALLINT,
    to_hour SMALLINT
);

CREATE TABLE alert_subscription (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    geozone_id INT REFERENCES geozone (gid) NOT NULL
);
