/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strtrim.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/01 20:34:42 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/12 21:52:44 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	get_end_index(char const *s1, char const *set,
	size_t start_index)
{
	size_t	i;

	i = ft_strlen(s1);
	while (i > start_index && ft_strchr(set, s1[i]))
		i--;
	return (i);
}

static size_t	get_start_index(char const *s1, char const *set)
{
	size_t	i;

	i = 0;
	while (s1[i] && ft_strchr(set, s1[i]))
		i++;
	return (i);
}

char	*ft_strtrim(char const *s1, char const *set)
{
	size_t	start_index;
	size_t	end_index;

	if (!s1 || !set)
		return (NULL);
	start_index = get_start_index(s1, set);
	end_index = get_end_index(s1, set, start_index);
	return (ft_substr(s1, start_index, end_index - start_index + 1));
}
