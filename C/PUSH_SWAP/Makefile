NAME =  push_swap

CC = cc
CFLAGS = -Wall -Wextra -Werror
RM = rm -f

SRCS_DIR = srcs
INCLUDE_DIR = include
MYLIB_DIR = mylib

SRCS = $(SRCS_DIR)/main.c \
		$(SRCS_DIR)/parse.c \
		$(SRCS_DIR)/init_stack.c \
		$(SRCS_DIR)/init_list.c \
		$(SRCS_DIR)/normalize.c \
		$(SRCS_DIR)/check_error.c \
		$(SRCS_DIR)/operations/pa.c \
		$(SRCS_DIR)/operations/pb.c \
		$(SRCS_DIR)/operations/sa.c \
		$(SRCS_DIR)/operations/ra.c \
		$(SRCS_DIR)/operations/rra.c \
		$(SRCS_DIR)/algorithms/quicksort.c \
		$(SRCS_DIR)/algorithms/radix_sort.c \
		$(SRCS_DIR)/algorithms/selectionsort_3.c \
		$(SRCS_DIR)/algorithms/selectionsort_4_5.c \
		$(SRCS_DIR)/algorithms/sort_a.c

OBJS = $(SRCS:.c=.o)
MYLIB = $(MYLIB_DIR)/mylib.a
HEADERS = $(INCLUDE_DIR)/push_swap.h
INCLUDES = -I$(INCLUDE_DIR) -I$(MYLIB_DIR)/include

all: $(NAME)

$(MYLIB):
	@$(MAKE) -C $(MYLIB_DIR)

$(NAME): $(MYLIB) $(OBJS)
	@$(CC) $(CFLAGS) $(OBJS) $(MYLIB) -o $(NAME)
	@echo "✓ $(NAME) created"

%.o: %.c $(HEADERS)
	@$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	@$(MAKE) -C $(MYLIB_DIR) clean
	@$(RM) $(OBJS)
	@echo "✓ Object files removed"

fclean: clean
	@$(MAKE) -C $(MYLIB_DIR) fclean
	@$(RM) $(NAME)
	@echo "✓ $(NAME) removed"

re: fclean all

.PHONY: all clean fclean re
