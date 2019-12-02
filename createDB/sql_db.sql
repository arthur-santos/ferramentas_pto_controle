BEGIN;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE USER controle_pto WITH PASSWORD 'controle_pto';

CREATE SCHEMA controle;

CREATE TABLE controle.tipo_situacao(
	id SERIAL NOT NULL PRIMARY KEY,
	nome VARCHAR(255) NOT NULL
);

INSERT INTO controle.tipo_situacao (nome) VALUES
('Não medido'),
('Reserva'),
('Não acessível'),
('Aguardando avaliação'),
('Aprovado'),
('Reprovado');

CREATE TABLE controle.ponto_controle_p(
	id serial NOT NULL,
  nome varchar(255) NOT NULL,
  mi varchar(255) NOT NULL,
  medidor varchar(255), 
  data_medicao timestamp with time zone,
	tipo_situacao_id INTEGER NOT NULL REFERENCES controle.tipo_situacao (id),
	equipe_medicao varchar(255),
	geom geometry(POINT, 31982),
	CONSTRAINT ponto_controle_p_pk PRIMARY KEY (id)
	 WITH (FILLFACTOR = 80)
);

CREATE TABLE controle.trilha_l(
	id serial NOT NULL,
	geom geometry(LINESTRING, 31982),
	CONSTRAINT trilha_l_pk PRIMARY KEY (id)
	 WITH (FILLFACTOR = 80)
);

CREATE TABLE controle.medicao_mi_a(
   id serial NOT NULL,
   mi varchar(255) NOT NULL,
   lote varchar(255),
   equipe varchar(255),
   pontos_medidos SMALLINT NOT NULL,
   total_pontos SMALLINT NOT NULL,
   geom geometry(POLYGON, 31982),
   CONSTRAINT medicao_mi_a_pk PRIMARY KEY (id)
     WITH (FILLFACTOR = 80)
);

GRANT USAGE ON SCHEMA controle TO controle_pto;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA controle TO controle_pto;
GRANT ALL ON ALL SEQUENCES IN SCHEMA controle TO controle_pto;

CREATE OR REPLACE FUNCTION controle.atualiza_grade_mi()
  RETURNS trigger AS
$BODY$
  BEGIN
    UPDATE controle.medicao_mi_a AS m
    SET total_pontos = g.total_pontos
    FROM (SELECT m.mi, count(p.geom) AS total_pontos 
    FROM controle.medicao_mi_a AS m LEFT JOIN controle.ponto_controle_p AS p 
    ON st_contains(m.geom,p.geom)
    GROUP BY m.mi) AS g
    WHERE m.mi = g.mi;

    UPDATE controle.medicao_mi_a AS m
    SET pontos_medidos = g.pontos_medidos
    FROM (SELECT m.mi, count(p.geom) AS pontos_medidos 
    FROM controle.medicao_mi_a AS m LEFT JOIN controle.ponto_controle_p AS p 
    ON st_contains(m.geom,p.geom)
    WHERE p.tipo_situacao_id IN (4, 5)
    GROUP BY m.mi) AS g
    WHERE m.mi = g.mi;

    RETURN NULL;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION controle.atualiza_grade_mi()
  OWNER TO postgres;

CREATE TRIGGER atualiza_grade_mi
AFTER UPDATE OR INSERT OR DELETE ON controle.ponto_controle_p
FOR EACH STATEMENT EXECUTE PROCEDURE controle.atualiza_grade_mi();


COMMIT;