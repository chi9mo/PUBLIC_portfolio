/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_hexlower.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/19 16:49:05 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/19 19:16:53 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static void	ft_store_hex(unsigned int nbr, char *base, char *result, size_t len)
{
	if (nbr == 0)
		result[0] = base[0];
	else
	{
		while (nbr > 0)
		{
			result[len] = base[nbr % 16];
			nbr /= 16;
			len--;
		}
	}
}

static char	*ft_dex_to_hex(unsigned int nbr, char *base)
{
	char			*result;
	size_t			len;
	unsigned int	temp;

	if (!base)
		return (NULL);
	len = 0;
	temp = nbr;
	if (nbr == 0)
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
	ft_store_hex(nbr, base, result, len);
	return (result);
}

int	ft_printf_hexlower(va_list ap)
{
	unsigned int	nbr;
	char			*str;
	size_t			len;

	nbr = va_arg(ap, unsigned int);
	str = ft_dex_to_hex(nbr, "0123456789abcdef");
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
