CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuidv4() PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    custom BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (user_id, name)
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS set_types (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    type TEXT NOT NULL,

    UNIQUE (user_id, type)
);

CREATE TABLE IF NOT EXISTS sets (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(id),
    exercise_id INT NOT NULL REFERENCES exercises(id),
    set_type_id INT NOT NULL REFERENCES set_types(id),
    number INT NOT NULL CHECK (number >= 0),
    reps INT NOT NULL CHECK (reps > 0),
    weight NUMERIC(6,2) NOT NULL CHECK (weight >= 0),
    rpe INT CHECK (rpe BETWEEN 1 AND 10),
    rir INT CHECK (rir >= 0),
    notes TEXT
);