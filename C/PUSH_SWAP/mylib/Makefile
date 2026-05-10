NAME = mylib.a

CC = cc
CFLAGS = -Wall -Wextra -Werror
AR = ar rcs
RM = rm -f

INCDIR = include
LIBFT_DIR = src/libft
PRINTF_DIR = src/ft_printf

LIBFT_SRCS = $(LIBFT_DIR)/ft_atoi.c \
		$(LIBFT_DIR)/ft_atol.c \
		$(LIBFT_DIR)/ft_bzero.c \
		$(LIBFT_DIR)/ft_calloc.c \
		$(LIBFT_DIR)/ft_isalnum.c \
		$(LIBFT_DIR)/ft_isalpha.c \
		$(LIBFT_DIR)/ft_isascii.c \
		$(LIBFT_DIR)/ft_isdigit.c \
		$(LIBFT_DIR)/ft_isprint.c \
		$(LIBFT_DIR)/ft_itoa.c \
		$(LIBFT_DIR)/ft_memchr.c \
		$(LIBFT_DIR)/ft_memcmp.c \
		$(LIBFT_DIR)/ft_memcpy.c \
		$(LIBFT_DIR)/ft_memmove.c \
		$(LIBFT_DIR)/ft_memset.c \
		$(LIBFT_DIR)/ft_putchar_fd.c \
		$(LIBFT_DIR)/ft_putendl_fd.c \
		$(LIBFT_DIR)/ft_putnbr_fd.c \
		$(LIBFT_DIR)/ft_putstr_fd.c \
		$(LIBFT_DIR)/ft_split.c \
		$(LIBFT_DIR)/ft_strchr.c \
		$(LIBFT_DIR)/ft_strdup.c \
		$(LIBFT_DIR)/ft_striteri.c \
		$(LIBFT_DIR)/ft_strjoin.c \
		$(LIBFT_DIR)/ft_strlcat.c \
		$(LIBFT_DIR)/ft_strlcpy.c \
		$(LIBFT_DIR)/ft_strlen.c \
		$(LIBFT_DIR)/ft_strmapi.c \
		$(LIBFT_DIR)/ft_strncmp.c \
		$(LIBFT_DIR)/ft_strnstr.c \
		$(LIBFT_DIR)/ft_strrchr.c \
		$(LIBFT_DIR)/ft_strtrim.c \
		$(LIBFT_DIR)/ft_substr.c \
		$(LIBFT_DIR)/ft_tolower.c \
		$(LIBFT_DIR)/ft_toupper.c

PRINTF_SRCS = $(PRINTF_DIR)/ft_printf.c \
		$(PRINTF_DIR)/ft_printf_char.c \
		$(PRINTF_DIR)/ft_printf_decimal.c \
		$(PRINTF_DIR)/ft_printf_hexlower.c \
		$(PRINTF_DIR)/ft_printf_hexupper.c \
		$(PRINTF_DIR)/ft_printf_str.c \
		$(PRINTF_DIR)/ft_printf_unsigned_d.c \
		$(PRINTF_DIR)/ft_printf_vptr.c

OBJS = $(LIBFT_SRCS:.c=.o) $(PRINTF_SRCS:.c=.o)

HEADERS = $(INCDIR)/libft.h \
		$(INCDIR)/ft_printf.h

all: $(NAME)

$(NAME): $(OBJS)
	@$(AR) $(NAME) $(OBJS)
	@echo "MYLIB: $(NAME) created successfully!"

%.o: %.c $(HEADERS)
	@$(CC) $(CFLAGS) -I$(INCDIR) -c $< -o $@

# norm:
# 	@norminette $(LIBFT_SRCS) $(PRINTF_SRCS) $(HEADERS)

clean:
	@$(RM) $(OBJS)
	@echo "MYLIB: Object files removed."

fclean: clean
	@$(RM) $(NAME)
	@echo "MYLIB: $(NAME) removed."

re: fclean all

.PHONY: all norm clean fclean re
