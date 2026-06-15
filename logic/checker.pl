% ----------------------------
% Propositional Logic Checker
% ----------------------------

% lookup_var(+Atom, +Valuation, -Value)
lookup_var(P, [P-V | _], V).
lookup_var(P, [_ | Rest], V) :-
    lookup_var(P, Rest, V).

% eval(+Formula, +Valuation, -TruthValue)

eval(P, Valuation, V) :-
    atom(P),
    lookup_var(P, Valuation, V).

eval(not(A), Valuation, true) :-
    eval(A, Valuation, false).
eval(not(A), Valuation, false) :-
    eval(A, Valuation, true).

eval(and(A,B), Valuation, true) :-
    eval(A, Valuation, true),
    eval(B, Valuation, true).
eval(and(A,B), Valuation, false) :-
    eval(A, Valuation, false);
    eval(B, Valuation, false).

eval(or(A,B), Valuation, true) :-
    eval(A, Valuation, true);
    eval(B, Valuation, true).
eval(or(A,B), Valuation, false) :-
    eval(A, Valuation, false),
    eval(B, Valuation, false).

eval(imp(A,B), Valuation, false) :-
    eval(A, Valuation, true),
    eval(B, Valuation, false).
eval(imp(A,B), Valuation, true) :-
    eval(A, Valuation, false);
    eval(B, Valuation, true).

eval(iff(A,B), Valuation, true) :-
    eval(A, Valuation, VA),
    eval(B, Valuation, VB),
    VA = VB.
eval(iff(A,B), Valuation, false) :-
    eval(A, Valuation, VA),
    eval(B, Valuation, VB),
    VA \= VB.

% ----------------------------
% Variable extraction
% ----------------------------

vars(F, Vars) :-
    collect_vars(F, RawVars),
    sort(RawVars, Vars).

collect_vars(F, [F]) :-
    atom(F).

collect_vars(not(A), Vars) :-
    collect_vars(A, Vars).

collect_vars(and(A,B), Vars) :-
    collect_vars(A, VA),
    collect_vars(B, VB),
    append(VA, VB, Vars).

collect_vars(or(A,B), Vars) :-
    collect_vars(A, VA),
    collect_vars(B, VB),
    append(VA, VB, Vars).

collect_vars(imp(A,B), Vars) :-
    collect_vars(A, VA),
    collect_vars(B, VB),
    append(VA, VB, Vars).

collect_vars(iff(A,B), Vars) :-
    collect_vars(A, VA),
    collect_vars(B, VB),
    append(VA, VB, Vars).

collect_vars([], []).
collect_vars([F | Rest], Vars) :-
    collect_vars(F, VF),
    collect_vars(Rest, VR),
    append(VF, VR, Vars).

% ----------------------------
% Valuation generation
% ----------------------------

valuations([], []).
valuations([P | Rest], [P-true | VRest]) :-
    valuations(Rest, VRest).
valuations([P | Rest], [P-false | VRest]) :-
    valuations(Rest, VRest).

% ----------------------------
% Classification
% ----------------------------

valid(F) :-
    vars(F, Vars),
    \+ (
        valuations(Vars, Valuation),
        eval(F, Valuation, false)
    ).

unsatisfiable(F) :-
    vars(F, Vars),
    \+ (
        valuations(Vars, Valuation),
        eval(F, Valuation, true)
    ).

contingent(F) :-
    vars(F, Vars),
    valuations(Vars, V1),
    eval(F, V1, true),
    valuations(Vars, V2),
    eval(F, V2, false).

classify(F, valid) :-
    valid(F), !.

classify(F, unsatisfiable) :-
    unsatisfiable(F), !.

classify(F, contingent) :-
    contingent(F), !.

% ----------------------------
% Equivalence
% ----------------------------

equivalent(A, B) :-
    vars([A, B], Vars),
    \+ (
        valuations(Vars, Valuation),
        eval(A, Valuation, VA),
        eval(B, Valuation, VB),
        VA \= VB
    ).

% ----------------------------
% Entailment
% ----------------------------

all_true([], _).
all_true([F | Rest], Valuation) :-
    eval(F, Valuation, true),
    all_true(Rest, Valuation).

entails(Premises, Conclusion) :-
    vars([Premises, Conclusion], Vars),
    \+ (
        valuations(Vars, Valuation),
        all_true(Premises, Valuation),
        eval(Conclusion, Valuation, false)
    ).

% ----------------------------
% Consistency
% ----------------------------

consistent(Set) :-
    vars(Set, Vars),
    valuations(Vars, Valuation),
    all_true(Set, Valuation).

consistent_with(F, Set) :-
    consistent([F | Set]).
    