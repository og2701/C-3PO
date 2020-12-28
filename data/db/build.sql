CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY_KEY,
	Prefix text DEFAULT "%"
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY, 
	XP integer DEFAULT 0
);