
typedef i32 int 
struct Character {
    1:string name,
    2:double id,
    3:int breedId,
    4:int serverId,
}
typedef list<Character> CharacterList
service Pyd2botService {
    CharacterList fetchAccountCharacters(1: string login, 2: string password, 3: int certId, 4: string certHash),
    oneway void runSession(1: string login, 2: string password, 3: int certId, 4: string certHash, 5:string sessionJson) ,
}
       
       