
typedef i32 int 
struct Charachter {
    1:string name,
    2:string id,
    3:string serverId,
}
typedef list<Charachter> CharachterList
service Pyd2botService {
    CharachterList fetchAccountCharachters(1: string login, 2: string password, 3: string certId, 4: string certHash),
    oneway void runSession(1: string login, 2: string password, 3: string certId, 4: string certHash, 5:string sessionId) ,
}
       
       