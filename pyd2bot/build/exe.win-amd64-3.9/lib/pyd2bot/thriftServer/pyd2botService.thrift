
typedef i32 int 
struct Character {
    1:string name,
    2:string id,
    3:string serverId,
}
typedef list<Character> CharacterList
service Pyd2botService {
    CharacterList fetchAccountCharacters(1: string login, 2: string password, 3: string certId, 4: string certHash),
    oneway void runSession(1: string login, 2: string password, 3: string certId, 4: string certHash, 5:string sessionJson) ,
}
       
       