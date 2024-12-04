CREATE DATABASE GestionVehicular;
USE GestionVehicular;

-- Tabla para personas
CREATE TABLE Persona (
    ID_Persona INT AUTO_INCREMENT PRIMARY KEY,
    Nombre_Persona VARCHAR(100) NOT NULL
);

-- Tabla para vehículos
CREATE TABLE Vehiculo (
    ID_Vehiculo INT AUTO_INCREMENT PRIMARY KEY,
    ID_Persona INT NOT NULL,
    Marca VARCHAR(50) NOT NULL,
    Modelo VARCHAR(50) NOT NULL,
    Unidad INT NOT NULL CHECK (Unidad >= 0),
    FOREIGN KEY (ID_Persona) REFERENCES Persona(ID_Persona)
);
