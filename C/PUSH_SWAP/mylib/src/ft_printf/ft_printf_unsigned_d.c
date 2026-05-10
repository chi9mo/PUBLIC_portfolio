/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_unsigned_d.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/19 11:59:12 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/19 15:37:52 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static void	store_int(unsigned int n, int digits, char *result)
{
	result[digits] = '\0';
	if (n == 0)
		result[0] = '0';
	else
	{
		while (n != 0)
		{
			result[digits - 1] = n % 10 + '0';
			n = n / 10;
			digits--;
		}
	}
}

static int	count_digits(unsigned int n)
{
	int	result;

	if (n == 0)
		return (1);
	result = 0;
	while (n != 0)
	{
		n = n / 10;
		result++;
	}
	return (result);
}

static char	*ft_uitoa(unsigned int n)
{
	char		*result;
	int			digits;

	digits = 0;
	digits = digits + count_digits(n);
	result = malloc(digits + 1);
	if (result == NULL)
		return (NULL);
	store_int(n, digits, result);
	return (result);
}

int	ft_printf_unsigned_d(va_list ap)
{
	unsigned int	num;
	char			*str;
	size_t			len;

	num = va_arg(ap, unsigned int);
	str = ft_uitoa(num);
	if (!str)
		return (-1);
	len = ft_strlen(str);
	if (write(1, str, len) == -1)
	{
		free(str);
		return (-1);
	}
	free(str);
	return (len);
}
