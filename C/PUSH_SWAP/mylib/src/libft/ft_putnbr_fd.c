/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_putnbr_fd.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/09 17:01:55 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/12 21:51:52 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	ft_check_n(int n, int fd)
{
	if (n == INT_MIN)
	{
		write(fd, "-2147483648", 11);
		return (1);
	}
	else if (n == 0)
	{
		write(fd, "0", 1);
		return (1);
	}
	return (0);
}

void	ft_putnbr_fd(int n, int fd)
{
	int		temp;
	int		digits;
	char	str[12];

	if (ft_check_n(n, fd))
		return ;
	digits = 0;
	if (n < 0)
	{
		str[digits++] = '-';
		n = -n;
	}
	temp = n;
	while (temp > 0)
	{
		temp = temp / 10;
		digits++;
	}
	str[digits] = '\0';
	while (n > 0)
	{
		str[--digits] = n % 10 + '0';
		n = n / 10;
	}
	ft_putstr_fd(str, fd);
}
