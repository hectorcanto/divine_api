SELECT 'CREATE DATABASE divine_local'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'divine_local'
)\gexec