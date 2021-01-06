CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY_KEY,
	Prefix text DEFAULT "%"
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY, 
	XP integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS achievements (
	UserID integer PRIMARY KEY, 
	a_points integer DEFAULT 0,
	a_rebelscum integer DEFAULT 0
);