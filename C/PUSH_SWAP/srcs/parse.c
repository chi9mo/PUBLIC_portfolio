/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 22:13:33 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/13 06:53:26 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	*convert_to_values(char **split, int size)
{
	int	*values;
	int	i;

	values = malloc(size * sizeof(int));
	if (!values)
		return (NULL);
	i = 0;
	while (i < size)
	{
		values[i] = ft_atoi(split[i]);
		i++;
	}
	return (values);
}

static int	count_strings(char **strs)
{
	int	count;

	count = 0;
	while (strs[count])
		count++;
	return (count);
}

static void	free_split(char **split)
{
	int	i;

	if (!split)
		return ;
	i = 0;
	while (split[i])
	{
		free(split[i]);
		i++;
	}
	free(split);
}

int	*parse_string(char *str, int *size)
{
	int		*values;
	char	**split;

	split = ft_split(str, ' ');
	if (!split)
		return (NULL);
	*size = count_strings(split);
	if (*size <= 0 || !validate_args(split, *size))
	{
		free_split(split);
		return (NULL);
	}
	values = convert_to_values(split, *size);
	free_split(split);
	if (!values || !check_duplication(values, *size))
	{
		if (values)
			free (values);
		return (NULL);
	}
	return (values);
}

int	*parse_clarg(int argc, char **argv, int *size)
{
	int	*values;
	int	i;

	*size = argc - 1;
	if (!validate_args(argv + 1, *size))
		return (NULL);
	values = malloc(*size * sizeof(int));
	if (!values)
		return (NULL);
	i = 0;
	while (i < *size)
	{
		values[i] = ft_atoi(argv[i + 1]);
		i++;
	}
	if (!check_duplication(values, *size))
		return (free(values), NULL);
	return (values);
}
