main_file=start

token_file=token_save

re:
	chmod +x $(main_file)

start: re
	./start

clean:
	rm $(token_file)
