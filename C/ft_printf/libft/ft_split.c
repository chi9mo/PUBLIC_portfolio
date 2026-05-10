/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/06 22:35:01 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/12 21:52:00 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static void	*free_all(char **strings, size_t end)
{
	size_t	i;

	i = 0;
	while (i <= end)
	{
		free(strings[i]);
		i++;
	}
	free(strings);
	return (NULL);
}

static char	**store_strings(char **strings, char const *s, char c)
{
	size_t	start_pos;
	size_t	len;
	size_t	i;

	start_pos = 0;
	i = 0;
	while (s[start_pos])
	{
		if (s[start_pos] == c)
			start_pos++;
		else
		{
			len = 0;
			while (s[start_pos + len] != c && s[start_pos + len] != '\0')
				len++;
			strings[i] = (char *)malloc(((len + 1) * sizeof(char)));
			if (strings[i] == NULL)
				return (free_all(strings, i));
			ft_strlcpy(strings[i], s + start_pos, len + 1);
			start_pos += len;
			i++;
		}
	}
	return (strings);
}

static size_t	count_strings(char const *s, char c)
{
	int		flag;
	size_t	count;

	flag = 0;
	count = 0;
	while (*s)
	{
		if (*s != c)
			flag = 1;
		if (*s == c && flag == 1)
		{
			count++;
			flag = 0;
		}
		s++;
	}
	return (count + flag);
}

char	**ft_split(char const *s, char c)
{
	char	**strings;
	size_t	count;

	if (s == NULL)
		return (NULL);
	count = count_strings(s, c);
	strings = (char **)malloc((count + 1) * sizeof(char *));
	if (strings == NULL)
		return (NULL);
	strings[count] = NULL;
	if (store_strings(strings, s, c) == NULL)
		return (NULL);
	return (strings);
}
