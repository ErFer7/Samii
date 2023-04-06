-- Create a new database called 'SamiiDatabase'
CREATE DATABASE SamiiDatabase;

CREATE TABLE Guild (
    ID INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    kick BOOLEAN NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Meeting (
    ID INT NOT NULL,
    GuildID INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (GuildID) REFERENCES Guild(ID)
);

CREATE TABLE Topic (
    ID INT NOT NULL,
    MeetingID INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Duration INT,
    PRIMARY KEY (ID),
    FOREIGN KEY (MeetingID) REFERENCES Meeting(ID)
);

CREATE TABLE User (
    ID INT NOT NULL,
    MeetingID INT NOT NULL,
    Username VARCHAR(255) NOT NULL,
    Name VARCHAR(255),
    PRIMARY KEY (ID),
    FOREIGN KEY (MeetingID) REFERENCES Meeting(ID)
);

CREATE TABLE UserPresence (
    StartTime TIMESTAMP NOT NULL,
    userID INT NOT NULL,
    MeetingID INT NOT NULL,
    PRIMARY KEY (StartTime),
    FOREIGN KEY (userID) REFERENCES User(ID),
    FOREIGN KEY (MeetingID) REFERENCES Meeting(ID)
);
