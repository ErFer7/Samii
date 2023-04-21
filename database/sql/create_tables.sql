CREATE TABLE Guild (
    ID BIGINT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    MainTextChannelID BIGINT,
    MainVoiceChannelID BIGINT,
    Kick BOOLEAN NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Meeting (
    GuildID BIGINT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    FOREIGN KEY (GuildID) REFERENCES Guild(ID)
);

CREATE TABLE Topic (
    MeetingName VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Duration INT,
    FOREIGN KEY (MeetingName) REFERENCES Meeting(Name)
);

CREATE TABLE User (
    ID INT NOT NULL,
    MeetingName VARCHAR(255) NOT NULL,
    Username VARCHAR(255) NOT NULL,
    FOREIGN KEY (MeetingName) REFERENCES Meeting(Name)
);

CREATE TABLE UserPresence (
    StartTime TIMESTAMP NOT NULL,
    userID INT NOT NULL,
    MeetingName VARCHAR(255) NOT NULL,
    FOREIGN KEY (userID) REFERENCES User(ID),
    FOREIGN KEY (MeetingName) REFERENCES Meeting(Name)
);
