DOFUSINVOKER = $(LOCALAPPDATA)/Ankama/Dofus/DofusInvoker.swf
FFDEC = $(CURDIR)/FFDec/ffdec.bat
DOFUS_SRC = $(CURDIR)/protocolBuilder/sources
SELECTCLASS = com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++
PYDOFUS_DIR = $(CURDIR)/pydofus2
PYD2BOT_DIR = $(CURDIR)/pyd2bot
PYD2BOTAPP_DIR = $(CURDIR)/pyd2botApp
PYD2BOT_DIST_DIR = "$(APPDATA)"/pyd2bot/

.ONESHELL:
.PHONY: setup
setup:
	python -m venv .venv
	source .venv/Scripts/activate
	pip install --upgrade pip
	pip install --upgrade setuptools
	echo "$(PYDOFUS_DIR)" >> .venv/pydofus2.pth
	echo "$(PYD2BOT_DIR)" >> .venv/pyd2bot.pth
	pip install -r requirements.txt

update: gen-protocol gen-msgClasses gen-msgShuffle extract-keys unpack-maps bdist

decompile:
	@$(FFDEC) -config parallelSpeedUp=true -selectclass $(SELECTCLASS) -export script $(DOFUS_SRC) $(DOFUSINVOKER)

.ONESHELL:

extract-keys:
	@$(FFDEC) -config parallelSpeedUp=true -export binaryData $(PYDOFUS_DIR)/binaryData $(DOFUSINVOKER)

gen-protocol:
	source .venv/Scripts/activate
	@echo "Generating protocol..."
	@python protocolBuilder/protocolParser.py $(DOFUS_SRC)
	@echo "Protocol generated"

gen-msgClasses:
	source .venv/Scripts/activate
	@echo "Generating msgClasses..."
	@python protocolBuilder/exportClasses.py
	@echo "msgClasses generated"

gen-msgShuffle:
	source .venv/Scripts/activate
	@echo "Generating msgShuffle..."
	@python protocolBuilder/extractMsgShuffle.py $(DOFUS_SRC)/scripts/com/ankamagames/dofus/network/MessageReceiver.as
	@echo "msgShuffle generated"

unpack-maps:
	source .venv/Scripts/activate
	@echo "Unpacking maps..."
	@python scripts/unpack_maps.py $(DOFUS_SRC)
	@echo "Maps unpacked"

deps:
	source .venv/Scripts/activate
	@pip install -r requirements.txt

sniff:
	source .venv/Scripts/activate
	@python -m snifferApp 

bdist:
	@cd $(PYD2BOT_DIR)
	@python -m venv .buildEnv
	@source .buildEnv/Scripts/activate
	@cd $(PYDOFUS_DIR)
	@python -m pip install --upgrade pip
	@pip install wheel
	@pip install .
	@cd $(PYD2BOT_DIR)
	@pip install -r requirements.txt
	@python build.py build
	@cp -a $(PYD2BOT_DIR)/build/exe.win-amd64-3.9/* $(PYD2BOT_DIST_DIR)

rebuild:
	@cd $(PYD2BOT_DIR)
	@source .buildEnv/Scripts/activate
	@python build.py build
	@cp -a $(PYD2BOT_DIR)/build/exe.win-amd64-3.9/* $(PYD2BOT_DIST_DIR)

serve:
	source .venv/Scripts/activate
	python $(CURDIR)/pyd2bot/pyd2bot.py

testClient:
	source .venv/Scripts/activate
	python $(CURDIR)/pyd2bot/pyd2bot/thriftServer/pyd2botClient.py

run:
	cd pyd2botApp
	npm start

gen-thrift:
	cd $(PYD2BOT_DIR)/pyd2bot/thriftServer
	./thrift-0.16.0.exe -r --gen js:node $(PYD2BOT_DIR)/pyd2bot/thriftServer/pyd2botService.thrift
	rm -rf $(PYD2BOTAPP_DIR)/src/pyd2botService
	mv gen-nodejs $(PYD2BOTAPP_DIR)/src/pyd2botService
	./thrift-0.16.0.exe -r --gen py $(PYD2BOT_DIR)/pyd2bot/thriftServer/pyd2botService.thrift
	rm -rf pyd2botService
	mv gen-py/pyd2botService/ ./
	rm -rf gen-py
