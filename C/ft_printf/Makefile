NAME =  libftprintf.a

CC = cc
CFLAGS = -Wall -Wextra -Werror
AR = ar rcs
RM = rm -f

PRINTF_SRCS =	ft_printf.c \
		ft_printf_char.c \
		ft_printf_decimal.c \
		ft_printf_hexlower.c \
		ft_printf_hexupper.c \
		ft_printf_str.c \
		ft_printf_unsigned_d.c \
		ft_printf_vptr.c

OBJS = $(PRINTF_SRCS:.c=.o)

LIBFT_DIR = libft
LIBFT = $(LIBFT_DIR)/libft.a

HEADERS = ft_printf.h $(LIBFT_DIR)/libft.h
INCLUDES = -I. -I$(LIBFT_DIR)

all: $(NAME)

$(LIBFT):
	@$(MAKE) -C $(LIBFT_DIR)

$(NAME): $(LIBFT) $(OBJS)
	@cp $(LIBFT) $(NAME)
	@$(AR) $(NAME) $(OBJS)
	@echo "✓ $(NAME) created successfully"

%.o: %.c $(HEADERS)
	@$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@
	@echo "✓ Compiled $<"

norm:
	@norminette $(PRINTF_SRCS) ft_printf.h
	@$(MAKE) -C $(LIBFT_DIR) norm

clean:
	@$(MAKE) -C $(LIBFT_DIR) clean
	@$(RM) $(OBJS)
	@echo "✓ Object files removed"

fclean: clean
	@$(MAKE) -C $(LIBFT_DIR) fclean
	@$(RM) $(NAME)
	@echo "✓ $(NAME) removed"

re: fclean all

.PHONY: all norm clean fclean re
