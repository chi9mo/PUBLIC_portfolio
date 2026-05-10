/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ra.c                                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/10 07:19:06 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/10 07:19:10 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	ra(t_stack *a)
{
	t_node	*tmp;

	if (!a->top || a->size <= 1)
		return ;
	tmp = a->top;
	a->top = a->top->next;
	a->top->prev = NULL;
	a->bottom->next = tmp;
	tmp->prev = a->bottom;
	tmp->next = NULL;
	a->bottom = tmp;
	ft_printf("ra\n");
}
