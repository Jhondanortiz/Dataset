-- Habilitar UTF-8
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Tabla 1: Fuentes (PDFs de origen)
CREATE TABLE IF NOT EXISTS sources (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500),
    publication_date DATE,
    organization VARCHAR(200),
    url TEXT,
    INDEX idx_filename (filename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 2: Grupos principales
CREATE TABLE IF NOT EXISTS groups (
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    group_name VARCHAR(200) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 3: Subgrupos
CREATE TABLE IF NOT EXISTS subgroups (
    subgroup_id INT PRIMARY KEY AUTO_INCREMENT,
    subgroup_name VARCHAR(200) NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
    UNIQUE KEY uq_subgroup (subgroup_name, group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 4: CWE
CREATE TABLE IF NOT EXISTS cwe (
    cwe_id VARCHAR(20) PRIMARY KEY,
    cwe_name VARCHAR(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 5: Vulnerabilidades principales
CREATE TABLE IF NOT EXISTS vulnerabilities (
    vuln_id INT PRIMARY KEY AUTO_INCREMENT,
    id INT NOT NULL UNIQUE,
    vulnerability_name VARCHAR(300),
    cve VARCHAR(50) UNIQUE,
    cwe_id VARCHAR(20),
    cvss_v4 DECIMAL(3,1),
    description TEXT,
    group_id INT NOT NULL,
    subgroup_id INT,
    FOREIGN KEY (cwe_id) REFERENCES cwe(cwe_id) ON DELETE SET NULL,
    FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (subgroup_id) REFERENCES subgroups(subgroup_id) ON DELETE SET NULL,
    INDEX idx_cve (cve),
    INDEX idx_group (group_id),
    INDEX idx_subgroup (subgroup_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 6: Relación Vulnerabilidad ↔ Fuente
CREATE TABLE IF NOT EXISTS vulnerability_sources (
    vuln_id INT NOT NULL,
    source_id INT NOT NULL,
    PRIMARY KEY (vuln_id, source_id),
    FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(vuln_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla 7: Vulnerabilidades Relacionadas
CREATE TABLE IF NOT EXISTS related_vulnerabilities (
    vuln_id INT NOT NULL,
    related_cve VARCHAR(50) NOT NULL,
    PRIMARY KEY (vuln_id, related_cve),
    FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(vuln_id) ON DELETE CASCADE,
    FOREIGN KEY (related_cve) REFERENCES vulnerabilities(cve) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
