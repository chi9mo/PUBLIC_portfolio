/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/11 21:14:37 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/20 21:47:16 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	identify_conversions(va_list ap, char conv)
{
	if (conv == 'c')
		return (ft_printf_char(ap));
	else if (conv == 's')
		return (ft_printf_str(ap));
	else if (conv == 'p')
		return (ft_printf_vptr(ap));
	else if (conv == 'd' || conv == 'i')
		return (ft_printf_decimal(ap));
	else if (conv == 'u')
		return (ft_printf_unsigned_d(ap));
	else if (conv == 'x')
		return (ft_printf_hexlower(ap));
	else if (conv == 'X')
		return (ft_printf_hexupper(ap));
	else if (conv == '%')
		return (write(1, "%", 1));
	return (0);
}

int	ft_printf(const char *format, ...)
{
	va_list	ap;
	size_t	i;
	size_t	count;

	va_start(ap, format);
	i = 0;
	count = 0;
	while (format[i])
	{
		if (format[i] == '%')
		{
			i++;
			count += identify_conversions(ap, format[i]);
			i++;
		}
		else
		{
			count += write(1, &format[i], 1);
			i++;
		}
	}
	va_end(ap);
	return (count);
}
