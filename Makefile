main_file=start

data_folder=./data/

re:
	chmod +x $(main_file)

start: re
	bash ./start

clean:
	rm -r $(data_folder)
