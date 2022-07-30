
typedef i32 int 
struct Spell {
    1:int id,
    2:string name
}
struct Character {
    1:string name,
    2:double id,
    3:int level,
    4:int breedId,
    5:string breedName,
    6:int serverId,
    7:string serverName
}
service Pyd2botService {
    list<Character> fetchAccountCharacters(1: string login, 2: string password, 3: int certId, 4: string certHash),
    oneway void runSession(1: string login, 2: string password, 3: int certId, 4: string certHash, 5:string sessionJson),
    list<Spell> fetchBreedSpells(1: int breedId),
    string fetchJobsInfosJson(),
    string recvMsgFromLeader(1: string msg)
}
       
    