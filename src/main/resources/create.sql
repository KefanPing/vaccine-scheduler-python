CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
)

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255),
    PRIMARY KEY (Time, Username),
    FOREIGN KEY (Username) REFERENCES Caregivers(Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE MakeReservation (
    Pname varchar(255),
    Vname varchar(255),
    Cname varchar(255),
    Time date,
    RID INT,
    PRIMARY KEY (RID),
    FOREIGN KEY (Pname) REFERENCES Patients(Username),
    FOREIGN KEY (Vname) REFERENCES Vaccines(Name),
    FOREIGN KEY (Cname) REFERENCES Caregivers(Username)
);


