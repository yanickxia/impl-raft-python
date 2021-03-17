from typing import List

import zerorpc
import random
from enum import Enum
from threading import Timer


class Role(Enum):
    Follower = 1
    Candidate = 2
    Leader = 3


class Message:
    pass


class Request(Message):
    pass


class Response(Message):
    pass


class RequestVote(Request):
    def __init__(self, term, candidate_id, last_log_index, last_log_term):
        self.term = term
        self.candidate_id = candidate_id
        self.last_log_index = last_log_index
        self.last_log_term = last_log_term


class ResponseVote(Response):
    def __init__(self, term, vote_granted):
        self.term = term
        self.vote_granted = vote_granted


class RaftServer(object):
    def __init__(self, server_id):
        self.servers = {}
        self.server_id = server_id

        #
        self.status = Role.Follower
        self.current_term = 0
        self.voted_for = None
        self.logs = []
        self.commit_index = 0
        self.last_applied = 0

        self.last_log_index = 0
        self.last_log_term = None
        # only in leader
        self.next_index = []
        self.match_index = []

        # helper
        self.timout_func = None

    def handle(self, req: Request):
        self.__start_election_timeout_func__()
        if type(req) == RequestVote:
            self.__handle_vote__(RequestVote(req))

        pass

    def run(self):
        self.__start_election_timeout_func__()

        pass

    def __start_election_timeout_func__(self):
        # rest timeout
        if self.timout_func is not None:
            self.timout_func.cancel()
        self.timout_func = Timer(random.randint(150, 300) / 1000, self.__election_timeout__)

    def __election_timeout__(self):
        self.status = Role.Candidate
        self.current_term += 1
        # vote
        vote = RequestVote(self.current_term, self.server_id, self.last_log_index, self.last_log_term)
        for server_id in self.servers:
            self.servers[server_id].handle(vote)

    def __handle_vote__(self, req: RequestVote):
        yes, no = ResponseVote(self.current_term, True), ResponseVote(self.current_term, False)
        if req.term < self.current_term:
            self.__send_message__(req.candidate_id, no)
            return
        if self.voted_for is None:
            self.voted_for = req.candidate_id
            self.__send_message__(req.candidate_id, yes)
            return
        if self.voted_for == req.candidate_id:
            self.__send_message__(req.candidate_id, yes)
            return

    def __send_message__(self, server_id, req: Message):
        self.servers[server_id].handle(req)
