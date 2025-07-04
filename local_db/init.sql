CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id TEXT,
    image_path TEXT,
    alt_en TEXT,
    alt_fr TEXT,
    alt_de TEXT,
    safety_en JSONB,
    safety_fr JSONB,
    safety_de JSONB,
    status TEXT DEFAULT 'pending',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
