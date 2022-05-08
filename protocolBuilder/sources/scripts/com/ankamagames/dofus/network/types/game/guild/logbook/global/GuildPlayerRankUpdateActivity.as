package com.ankamagames.dofus.network.types.game.guild.logbook.global
{
    import com.ankamagames.dofus.network.types.game.guild.GuildRankMinimalInformation;
    import com.ankamagames.dofus.network.types.game.guild.logbook.GuildLogbookEntryBasicInformation;
    import com.ankamagames.jerakine.network.ICustomDataInput;
    import com.ankamagames.jerakine.network.ICustomDataOutput;
    import com.ankamagames.jerakine.network.INetworkType;
    import com.ankamagames.jerakine.network.utils.FuncTree;
    
    public class GuildPlayerRankUpdateActivity extends GuildLogbookEntryBasicInformation implements INetworkType
    {
        
        public static const protocolId:uint = 6214;
         
        
        public var guildRankMinimalInfos:GuildRankMinimalInformation;
        
        public var playerId:Number = 0;
        
        public var playerName:String = "";
        
        private var _guildRankMinimalInfostree:FuncTree;
        
        public function GuildPlayerRankUpdateActivity()
        {
            this.guildRankMinimalInfos = new GuildRankMinimalInformation();
            super();
        }
        
        override public function getTypeId() : uint
        {
            return 6214;
        }
        
        public function initGuildPlayerRankUpdateActivity(id:uint = 0, date:Number = 0, guildRankMinimalInfos:GuildRankMinimalInformation = null, playerId:Number = 0, playerName:String = "") : GuildPlayerRankUpdateActivity
        {
            super.initGuildLogbookEntryBasicInformation(id,date);
            this.guildRankMinimalInfos = guildRankMinimalInfos;
            this.playerId = playerId;
            this.playerName = playerName;
            return this;
        }
        
        override public function reset() : void
        {
            super.reset();
            this.guildRankMinimalInfos = new GuildRankMinimalInformation();
            this.playerName = "";
        }
        
        override public function serialize(output:ICustomDataOutput) : void
        {
            this.serializeAs_GuildPlayerRankUpdateActivity(output);
        }
        
        public function serializeAs_GuildPlayerRankUpdateActivity(output:ICustomDataOutput) : void
        {
            super.serializeAs_GuildLogbookEntryBasicInformation(output);
            this.guildRankMinimalInfos.serializeAs_GuildRankMinimalInformation(output);
            if(this.playerId < 0 || this.playerId > 9007199254740992)
            {
                throw new Error("Forbidden value (" + this.playerId + ") on element playerId.");
            }
            output.writeVarLong(this.playerId);
            output.writeUTF(this.playerName);
        }
        
        override public function deserialize(input:ICustomDataInput) : void
        {
            this.deserializeAs_GuildPlayerRankUpdateActivity(input);
        }
        
        public function deserializeAs_GuildPlayerRankUpdateActivity(input:ICustomDataInput) : void
        {
            super.deserialize(input);
            this.guildRankMinimalInfos = new GuildRankMinimalInformation();
            this.guildRankMinimalInfos.deserialize(input);
            this._playerIdFunc(input);
            this._playerNameFunc(input);
        }
        
        override public function deserializeAsync(tree:FuncTree) : void
        {
            this.deserializeAsyncAs_GuildPlayerRankUpdateActivity(tree);
        }
        
        public function deserializeAsyncAs_GuildPlayerRankUpdateActivity(tree:FuncTree) : void
        {
            super.deserializeAsync(tree);
            this._guildRankMinimalInfostree = tree.addChild(this._guildRankMinimalInfostreeFunc);
            tree.addChild(this._playerIdFunc);
            tree.addChild(this._playerNameFunc);
        }
        
        private function _guildRankMinimalInfostreeFunc(input:ICustomDataInput) : void
        {
            this.guildRankMinimalInfos = new GuildRankMinimalInformation();
            this.guildRankMinimalInfos.deserializeAsync(this._guildRankMinimalInfostree);
        }
        
        private function _playerIdFunc(input:ICustomDataInput) : void
        {
            this.playerId = input.readVarUhLong();
            if(this.playerId < 0 || this.playerId > 9007199254740992)
            {
                throw new Error("Forbidden value (" + this.playerId + ") on element of GuildPlayerRankUpdateActivity.playerId.");
            }
        }
        
        private function _playerNameFunc(input:ICustomDataInput) : void
        {
            this.playerName = input.readUTF();
        }
    }
}
