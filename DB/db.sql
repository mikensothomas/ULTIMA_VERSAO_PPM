CREATE TABLE IF NOT EXISTS dados_passagem (
    id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    assento VARCHAR(10) NOT NULL,
    CONSTRAINT unique_assento_data_hora UNIQUE (data, hora, assento)
);