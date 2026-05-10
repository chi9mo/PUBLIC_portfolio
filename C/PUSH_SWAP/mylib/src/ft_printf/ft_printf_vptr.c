/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_vptr.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/20 20:08:37 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/20 21:39:01 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static void	ft_store_hex(uintptr_t unum, char *base, char *result, size_t len)
{
	if (unum == 0)
		result[0] = base[0];
	else
	{
		while (unum > 0)
		{
			result[len] = base[unum % 16];
			unum /= 16;
			len--;
		}
	}
}

static char	*ft_uint_to_hex(uintptr_t unum, char *base)
{
	char		*result;
	size_t		len;
	uintptr_t	temp;

	if (!base)
		return (NULL);
	len = 0;
	temp = unum;
	if (unum == 0)
		len = 1;
	else
	{
		while (temp > 0)
		{
			temp /= 16;
			len++;
		}
	}
	result = malloc(len + 1);
	if (!result)
		return (NULL);
	result[len--] = '\0';
	ft_store_hex(unum, base, result, len);
	return (result);
}

int	ft_printf_vptr(va_list ap)
{
	uintptr_t	unum;
	char		*str;
	size_t		len;

	unum = (uintptr_t)va_arg(ap, void *);
	str = ft_uint_to_hex(unum, "0123456789abcdef");
	if (!str)
		return (-1);
	else if (str[0] == '0')
	{
		free(str);
		return (write(1, "(nil)", 5));
	}
	else
	{
		write(1, "0x", 2);
		len = ft_strlen(str);
		if (write(1, str, len) == -1)
		{
			free(str);
			return (-1);
		}
		free(str);
		return (len + 2);
	}
}
