
typedef i32 int 
struct Charachter {
    1:string name,
    2:string id,
}
typedef list<Charachter> CharachterList
service Pyd2bot {
    oneway void setAccountCreds(1:string login, 2:string password, 3:string certId, 4:string certHash),
    CharachterList fetchAccountCharachters(),
    oneway void runSession(1:string sessionId),
}
       