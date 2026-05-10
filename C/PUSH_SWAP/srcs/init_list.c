/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   init_list.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/30 07:44:06 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:37:09 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static t_node	*create_node(int value, int index)
{
	t_node	*new_node;

	new_node = malloc(sizeof(t_node));
	if (!new_node)
		return (NULL);
	new_node->value = value;
	new_node->index = index;
	new_node->prev = NULL;
	new_node->next = NULL;
	return (new_node);
}

t_node	*create_list(int *values, int *indeces, int size)
{
	t_node	*list;
	t_node	*current_node;
	t_node	*new_node;
	int		i;

	if (size <= 0)
		return (NULL);
	list = create_node(values[0], indeces[0]);
	if (!list)
		return (NULL);
	current_node = list;
	i = 1;
	while (i < size)
	{
		new_node = create_node(values[i], indeces[i]);
		if (!new_node)
			return (NULL);
		current_node->next = new_node;
		new_node->prev = current_node;
		current_node = new_node;
		i++;
	}
	return (list);
}
