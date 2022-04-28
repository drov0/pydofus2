DOFUSINVOKER = $(LOCALAPPDATA)/Ankama/Dofus/DofusInvoker.swf
FFDEC = $(CURDIR)/FFDec/ffdec.bat
DOFUS_SRC = $(CURDIR)/protocolBuilder/sources
SELECTCLASS = com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++
PYDOFUS_DIR = $(CURDIR)/pydofus2
PYD2BOT_DIR = $(CURDIR)

.ONESHELL:
.PHONY: setup
setup:
	python -m venv .venv
	source .venv/Scripts/activate
	echo "$(PYDOFUS_DIR)" >> .venv/pydofus2.pth
	echo "$(PYD2BOT_DIR)" >> .venv/pyd2bot.pth
	pip install -r requirements.txt

update: decompile gen-protocol gen-msgClasses gen-msgShuffle extract-keys unpack-maps

decompile:
	@$(FFDEC) -config parallelSpeedUp=true -selectclass $(SELECTCLASS) -export script $(DOFUS_SRC) $(DOFUSINVOKER)

.ONESHELL:

extract-keys:
	@$(FFDEC) -config parallelSpeedUp=true -export binaryData $(PYDOFUS_DIR)/binaryData $(DOFUSINVOKER)

gen-protocol:
	@echo "Generating protocol..."
	@python protocolBuilder/protocolParser.py $(DOFUS_SRC)
	@echo "Protocol generated"

gen-msgClasses:
	@echo "Generating msgClasses..."
	@python protocolBuilder/exportClasses.py
	@echo "msgClasses generated"

gen-msgShuffle:
	@echo "Generating msgShuffle..."
	@python protocolBuilder/extractMsgShuffle.py $(DOFUS_SRC)/scripts/com/ankamagames/dofus/network/MessageReceiver.as
	@echo "msgShuffle generated"

unpack-maps:
	@echo "Unpacking maps..."
	@python scripts/unpack_maps.py $(DOFUS_SRC)
	@echo "Maps unpacked"

deps:
	@pip install -r requirements.txt

sniff:
	source .venv/Scripts/activate
	@python -m snifferApp 

activate:
	. .venv/Scripts/activate

createAccount:
	@python $(CURDIR)/launcher/CredsManager.py $(entryName) $(login) $(password)

createBot:
	@python $(CURDIR)/pyd2bot/managers/BotsDataManager.py $(botName) $(account) $(serverId) $(charachterId)

genKeys:
	@ssh-keygen -t rsa -b 2056 -m PEM -f $(PASS_ENC_KEYS)/id_rsa

test:
	source .venv/Scripts/activate
	@python $(CURDIR)/pyd2bot/main.py $(bot)

